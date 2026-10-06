import SwiftUI

struct MainWindowView: View {
    var body: some View {
        ZStack {
            BackgroundBlurView()
                .ignoresSafeArea()
            ContentView()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.clear)
    }
}
