import Foundation

struct AppConfig {
    // Static configuration - modify these values as needed
    static let encryptionSalt: String = "salt"
    static let serverURL: String = "http://localhost:8105"
    static let apiEndpoint: String = "/api/password"
    
    // Use user's home directory for write access (resolved at runtime)
    static var passwordFilePath: String {
        return "\(NSHomeDirectory())/encrypted"
    }
}
