import Foundation
import AppKit

class PasswordVerifier {
    static let shared = PasswordVerifier()
    
    private init() {}
    
    /// Get the current macOS username
    func getCurrentUsername() -> String {
        return NSUserName()
    }
    
    /// Returns true if password is correct, false otherwise
    func verifyPassword(username: String, password: String) -> Bool {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/dscl")
        process.arguments = ["/Local/Default", "-authonly", username, password]
        
        // Capture stderr (dscl outputs errors to stderr)
        let pipe = Pipe()
        process.standardError = pipe
        process.standardOutput = pipe
        
        do {
            try process.run()
            process.waitUntilExit()
            
            // Read the output
            let data = pipe.fileHandleForReading.readDataToEndOfFile()
            let output = String(data: data, encoding: .utf8) ?? ""
            
            // If output is empty, authentication succeeded
            // If output contains error, authentication failed
            // Exit code 0 also indicates success
            let isEmpty = output.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
            let exitCode = process.terminationStatus
            
            return isEmpty && exitCode == 0
        } catch {
            print("Error executing password verification: \(error)")
            return false
        }
    }
}
