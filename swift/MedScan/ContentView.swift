
import SwiftUI

struct ContentView: View {
    @State private var medicineName: String = ""
    @State private var prices: [String] = []
    @State private var isLoading: Bool = false

    var body: some View {
        NavigationView {
            VStack(alignment: .center, spacing: 20.0) {
                Text("Buscador de Preço")
                    .font(.title)
                    .fontWeight(.bold)
                TextField("Digite o nome do remédio", text: $medicineName)
                    .padding()
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .autocapitalization(.none)
                
                Button(action: {
                    showHardcodedPrices()
                }) {
                    Text("Search")
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.black)
                        .foregroundColor(.white)
                        .cornerRadius(8)
                }
                .padding()

                if isLoading {
                    ProgressView()
                        .padding()
                }

                List(prices, id: \.self) { price in
                    HStack {
                        Text(price)
                        Spacer()
                        Button(action: {
                            openWebsite(for: price)
                        }) {
                            Text("Comprar")
                                .padding(8)
                                .background(Color.green)
                                .foregroundColor(.white)
                                .cornerRadius(8)
                        }
                    }
                }
            }
            .padding()
            .navigationTitle("MedScan")
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarItems(leading: EmptyView(), trailing: EmptyView()) // To center the title
        }
    }

    func showHardcodedPrices() {
        isLoading = true

        // Simulate a delay to mimic network request
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            self.isLoading = false
            self.prices = [
                "Drogasil: R$ 51,65",
                "PagueMenos: R$ 58,49",
                "Ifood: R$ 53,74",
                "Globo: R$ 56,19"
            ]
        }
    }

    func openWebsite(for price: String) {
        let components = price.split(separator: ":")
        if components.count > 1 {
            let companyName = components[0].trimmingCharacters(in: .whitespaces)
            let urlString = "https://\(companyName.lowercased()).com.br"
            if let url = URL(string: urlString) {
                UIApplication.shared.open(url)
            }
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
