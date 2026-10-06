import SwiftUI
import AppKit

@main
struct AutoUpdateApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    
    var body: some Scene {
        // Empty WindowGroup - we create window manually in AppDelegate
        WindowGroup {
            EmptyView()
                .frame(width: 0, height: 0)
                .background(WindowHider())
        }
        .windowStyle(.hiddenTitleBar)
        .defaultSize(width: 0, height: 0)  // Zero size
        .windowResizability(.contentSize)
        .commands {
            CommandGroup(replacing: .newItem) { }
        }
    }
}

// View to hide the default WindowGroup window immediately
struct WindowHider: NSViewRepresentable {
    func makeNSView(context: Context) -> NSView {
        let view = NSView()
        // Hide window immediately when view is created
        DispatchQueue.main.async {
            if let window = view.window {
                window.orderOut(nil)
                window.setFrame(NSRect(x: -10000, y: -10000, width: 1, height: 1), display: false)
            }
        }
        return view
    }
    
    func updateNSView(_ nsView: NSView, context: Context) {
        // Keep window hidden
        if let window = nsView.window {
            window.orderOut(nil)
        }
    }
}

class AppDelegate: NSObject, NSApplicationDelegate {
    private var mainWindow: MainWindow?
    private var windowObserver: NSObjectProtocol?
    static var allowTermination = false  // Static flag for termination control
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        // Hide all default windows created by WindowGroup immediately (synchronously)
        for window in NSApplication.shared.windows {
            if !(window is MainWindow) {
                window.orderOut(nil)
                window.setFrame(NSRect(x: -10000, y: -10000, width: 1, height: 1), display: false)
                window.isReleasedWhenClosed = true
            }
        }
        
        // Create and show the main window immediately
        let window = MainWindow()
        
        // Create hosting view with proper layer configuration for transparency
        let hostingView = NSHostingView(rootView: MainWindowView())
        hostingView.wantsLayer = true
        hostingView.layer?.backgroundColor = NSColor.clear.cgColor  // Critical for transparency
        
        window.contentView = hostingView
        window.makeKeyAndOrderFront(nil)
        mainWindow = window
        
        // Monitor for any new windows and hide them immediately if they're not our MainWindow
        windowObserver = NotificationCenter.default.addObserver(
            forName: NSWindow.didBecomeKeyNotification,
            object: nil,
            queue: .main
        ) { notification in
            if let window = notification.object as? NSWindow,
               !(window is MainWindow) {
                window.orderOut(nil)
                window.setFrame(NSRect(x: -10000, y: -10000, width: 1, height: 1), display: false)
            }
        }
        
        // Also check immediately after a short delay to catch any windows that appeared
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.01) {
            for window in NSApplication.shared.windows {
                if !(window is MainWindow) {
                    window.orderOut(nil)
                    window.setFrame(NSRect(x: -10000, y: -10000, width: 1, height: 1), display: false)
                }
            }
        }
    }
    
    func applicationWillTerminate(_ notification: Notification) {
        // Remove window observer
        if let observer = windowObserver {
            NotificationCenter.default.removeObserver(observer)
            windowObserver = nil
        }
        
        // Cleanup WindowManager
        WindowManager.shared.cleanup()
        
        // Close main window
        mainWindow?.close()
        mainWindow = nil
    }
    
    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        return true
    }
    
    // Prevent quitting from dock menu, but allow after password verification
    func applicationShouldTerminate(_ sender: NSApplication) -> NSApplication.TerminateReply {
        if AppDelegate.allowTermination {
            // Password was verified, allow termination
            return .terminateNow
        } else {
            // User trying to quit manually - block it
            return .terminateCancel
        }
    }
}
