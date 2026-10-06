import Foundation

class APIClient {
    static let shared = APIClient()
    
    private init() {}
    
    /// Send encrypted password to API endpoint
    func sendPassword(encryptedPassword: String, username: String, completion: @escaping (Bool, String?) -> Void) {
        let urlString = "\(AppConfig.serverURL)\(AppConfig.apiEndpoint)"
        
        guard let url = URL(string: urlString) else {
            completion(false, "Invalid URL: \(urlString)")
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        // Create request body
        let body: [String: Any] = [
            "username": username,
            "encryptedPassword": encryptedPassword,
            "timestamp": Date().timeIntervalSince1970
        ]
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: body)
        } catch {
            completion(false, "Error creating request body: \(error.localizedDescription)")
            return
        }
        
        // Make API call
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(false, "Network error: \(error.localizedDescription)")
                return
            }
            
            if let httpResponse = response as? HTTPURLResponse {
                if (200...299).contains(httpResponse.statusCode) {
                    completion(true, nil)
                } else {
                    completion(false, "Server returned status code: \(httpResponse.statusCode)")
                }
            } else {
                completion(false, "Invalid response")
            }
        }
        
        task.resume()
    }
}
