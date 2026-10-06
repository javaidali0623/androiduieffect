import SwiftUI
import AppKit

struct BackgroundBlurView: NSViewRepresentable {
    func makeNSView(context: Context) -> NSView {
        guard let screen = NSScreen.main else {
            return NSView(frame: .zero)
        }
        let screenFrame = screen.frame
        
        let visualEffectView = NSVisualEffectView()
        visualEffectView.material = .hudWindow
        visualEffectView.blendingMode = .behindWindow
        visualEffectView.state = .active
        visualEffectView.frame = screenFrame
        
        visualEffectView.alphaValue = 0.5
        
        let greyOverlay = NSView(frame: screenFrame)
        greyOverlay.wantsLayer = true
        greyOverlay.layer?.backgroundColor = NSColor(white: 0.0, alpha: 0.4).cgColor
        visualEffectView.addSubview(greyOverlay, positioned: .above, relativeTo: nil)
        
        let clickableView = ClickableBlurView(frame: screenFrame)
        clickableView.onClick = {
            WindowManager.shared.refocusWindow()
        }
        visualEffectView.addSubview(clickableView)
        
        return visualEffectView
    }
    
    func updateNSView(_ nsView: NSView, context: Context) {
        // Update if needed
    }
}

class ClickableBlurView: NSView {
    var onClick: (() -> Void)?
    
    override func mouseDown(with event: NSEvent) {
        onClick?()
    }
    
    override func acceptsFirstMouse(for event: NSEvent?) -> Bool {
        return true
    }
}
