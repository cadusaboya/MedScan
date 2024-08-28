import SwiftUI

struct ContentView: View {
    var body: some View {
        TabView {
            // Main screen with navigation
            NavigationView {
                MainPageView()
                    .navigationTitle("Screen 1")
            }
            .tabItem {
                Label("Menu Principal", systemImage: "house")
            }
            
            // Screen 2
            NavigationView {
                BuscadorView()
                    .navigationTitle("Screen 2")
            }
            .tabItem {
                Label("Buscar", systemImage: "star")
            }

        }
    }
}

struct Content_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}

