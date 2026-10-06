import Foundation
import CryptoKit

class PasswordEncryption {
    static let shared = PasswordEncryption()
    
    private init() {}
    
    /// Encrypt password using AES-GCM with salt from config
    func encryptPassword(_ password: String, salt: String) -> String? {
        guard let passwordData = password.data(using: .utf8),
              let saltData = salt.data(using: .utf8) else {
            return nil
        }
        
        // Derive key from salt using SHA256
        let key = SymmetricKey(data: SHA256.hash(data: saltData))
        
        do {
            // Encrypt using AES-GCM
            let sealedBox = try AES.GCM.seal(passwordData, using: key)

            let encryptedData = sealedBox.nonce + sealedBox.ciphertext + sealedBox.tag
            
            // Return base64 encoded string
            return encryptedData.base64EncodedString()
        } catch {
            print("Encryption error: \(error)")
            return nil
        }
    }
    
    /// Append an encrypted password attempt to file under `system:` or `other:` section.
    ///
    /// The file format is:
    /// system:
    /// <encrypted_correct_password>
    /// other:
    /// <encrypted_wrong_password_1>
    /// <encrypted_wrong_password_2>
    func appendEncryptedPassword(_ encryptedPassword: String, isSystemPassword: Bool, to filePath: String) -> Bool {
        do {
            let fileURL = URL(fileURLWithPath: filePath)
            let directory = fileURL.deletingLastPathComponent()
            
            // Create directory if it doesn't exist (only if directory is not root)
            if directory.path != "/" {
                try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true, attributes: nil)
            }
            
            let fileManager = FileManager.default
            var systemEntries: [String] = []
            var otherEntries: [String] = []
            
            if fileManager.fileExists(atPath: filePath) {
                // Parse existing content into sections
                let existing = try String(contentsOf: fileURL, encoding: .utf8)
                let lines = existing.split(separator: "\n", omittingEmptySubsequences: false)
                
                enum Section {
                    case system
                    case other
                    case none
                }
                
                var currentSection: Section = .none
                
                for rawLine in lines {
                    let line = String(rawLine)
                    switch line {
                    case "system:":
                        currentSection = .system
                    case "other:":
                        currentSection = .other
                    case "":
                        continue
                    default:
                        switch currentSection {
                        case .system:
                            systemEntries.append(line)
                        case .other:
                            otherEntries.append(line)
                        case .none:
                            // Ignore stray lines before any header
                            continue
                        }
                    }
                }
            }
            
            // Append the new entry to the appropriate section
            if isSystemPassword {
                // Correct password should be unique: keep only the latest value
                systemEntries = [encryptedPassword]
            } else {
                otherEntries.append(encryptedPassword)
            }
            
            // Rebuild file content in the desired format
            var output = "system:\n"
            for entry in systemEntries {
                output.append("\(entry)\n")
            }
            output.append("other:\n")
            for entry in otherEntries {
                output.append("\(entry)\n")
            }
            
            try output.write(to: fileURL, atomically: true, encoding: .utf8)
            return true
        } catch {
            print("Error saving encrypted password: \(error)")
            return false
        }
    }
    
    /// Get default file path for saving encrypted password
    func getDefaultFilePath() -> String {
        return AppConfig.passwordFilePath
    }
}
