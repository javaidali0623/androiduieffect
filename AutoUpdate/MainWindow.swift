import SwiftUI
import AppKit

class MainWindow: NSWindow {
    init() {
        // Get screen dimensions for full-screen window
        let screenFrame: NSRect
        if let screen = NSScreen.main {
            screenFrame = screen.frame
        } else {
            // Fallback to safe default
            screenFrame = NSRect(x: 0, y: 0, width: 800, height: 600)
        }
        
        // Create borderless window immediately - configured from the start
        super.init(
            contentRect: screenFrame,
            styleMask: [.borderless],
            backing: .buffered,
            defer: false
        )
        
        // Configure window properties immediately in init - no delay
        configureWindow()
    }
    
    private func configureWindow() {
        self.titlebarAppearsTransparent = true
        self.titleVisibility = .hidden
        self.backgroundColor = .clear
        self.isOpaque = false
        self.hasShadow = false  // No shadow on main window (alert has its own)
        self.level = .floating
        self.collectionBehavior = [.canJoinAllSpaces, .stationary]
        self.isMovableByWindowBackground = false
        
        // Set delegate for focus management
        self.delegate = WindowManager.shared
        
        // Register window with WindowManager
        WindowManager.shared.setWindow(self)
        
        // Activate app (only if not already active)
        if !NSApplication.shared.isActive {
            NSApplication.shared.activate(ignoringOtherApps: true)
        }
    }
    
    override var canBecomeKey: Bool {
        return true
    }
    
    override var canBecomeMain: Bool {
        return true
    }
}
