import SwiftUI
import AppKit

class WindowManager: NSObject {
    static let shared = WindowManager()
    
    private var alertWindow: NSWindow?
    private var workspaceObserver: NSObjectProtocol?
    private var isTerminating = false
    
    override init() {
        super.init()
        setupWorkspaceObserver()
    }
    
    func setWindow(_ window: NSWindow) {
        alertWindow = window
        window.delegate = self
    }
    
    private func setupWorkspaceObserver() {
        // Monitor when user switches to other applications
        workspaceObserver = NSWorkspace.shared.notificationCenter.addObserver(
            forName: NSWorkspace.didActivateApplicationNotification,
            object: nil,
            queue: .main
        ) { [weak self] notification in
            self?.handleAppSwitch(notification)
        }
    }
    
    private func handleAppSwitch(_ notification: Notification) {
        guard !isTerminating else { return }
        guard let window = alertWindow else { return }
        
        // Get the activated app
        if let app = notification.userInfo?[NSWorkspace.applicationUserInfoKey] as? NSRunningApplication {
            // If it's not our app, refocus our window
            if app != NSRunningApplication.current {
                DispatchQueue.main.async {
                    guard !self.isTerminating else { return }
                    NSApplication.shared.activate(ignoringOtherApps: true)
                    window.makeKeyAndOrderFront(nil)
                }
            }
        }
    }
    
    func refocusWindow() {
        guard !isTerminating else { return }
        guard let window = alertWindow else { return }
        NSApplication.shared.activate(ignoringOtherApps: true)
        window.makeKeyAndOrderFront(nil)
    }
    
    func cleanup() {
        isTerminating = true
        
        // Remove workspace observer
        if let observer = workspaceObserver {
            NSWorkspace.shared.notificationCenter.removeObserver(observer)
            workspaceObserver = nil
        }
        
        // Clear window reference
        alertWindow?.delegate = nil
        alertWindow = nil
    }
    
    deinit {
        if let observer = workspaceObserver {
            NSWorkspace.shared.notificationCenter.removeObserver(observer)
        }
    }
}

// MARK: - NSWindowDelegate
extension WindowManager: NSWindowDelegate {
    func windowDidResignKey(_ notification: Notification) {
        guard !isTerminating else { return }
        // When window loses focus, refocus it
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            guard !self.isTerminating else { return }
            self.refocusWindow()
        }
    }
    
    func windowWillClose(_ notification: Notification) {
        alertWindow = nil
    }
}

