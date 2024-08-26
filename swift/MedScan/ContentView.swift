import SwiftUI
import SafariServices

struct PriceResponse: Codable {
    let name: String
    let lowest_price: Double
}

struct ContentView: View {
    @State private var medicineName: String = ""
    @State private var cep: String = ""
    @State private var drogasilPrice: Double?
    @State private var globoPrice: Double?
    @State private var pagueMenosPrice: Double?
    @State private var ifoodPrice: Double?
    @State private var isLoading: Bool = false
    @State private var showTable: Bool = false
    @State private var selectedProviderURL: URL?
    @State private var showSafari: Bool = false
    @State private var pendingRequests: Int = 0

    var body: some View {
        NavigationView {
            VStack(alignment: .center) {
                Text("Buscador de Preço")
                    .font(.title)
                    .fontWeight(.bold)
                    .padding(.vertical, 10.0)
                
                TextField("Digite o nome do remédio", text: $medicineName)
                    .padding(.horizontal)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .autocapitalization(.none)
                
                TextField("Digite a cidade", text: $cep)
                    .padding(.horizontal)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .keyboardType(.numberPad)
                    .autocapitalization(.none)

                Button(action: {
                    resetValues()
                    isLoading = true
                    showTable = false
                    pendingRequests = 4 // Number of providers
                    fetchPrices()
                }) {
                    Text("Buscar")
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.black)
                        .foregroundColor(.white)
                        .cornerRadius(8)
                }
                .padding()

                if showTable {
                    List {
                        ForEach(sortedPrices(), id: \.name) { provider in
                            priceRow(name: provider.name, price: provider.price, provider: provider.provider)
                        }
                    }
                }

                if isLoading {
                    VStack {
                        ProgressView()
                        Text("Buscando preços...")
                            .padding(.top, 10)
                    }
                }
            }
            .padding()
            .navigationTitle("MedScan")
            .navigationBarTitleDisplayMode(.inline)
            .sheet(isPresented: $showSafari) {
                if let url = selectedProviderURL {
                    SafariView(url: url)
                }
            }
        }
    }

    func resetValues() {
        drogasilPrice = nil
        globoPrice = nil
        pagueMenosPrice = nil
        ifoodPrice = nil
    }

    func fetchPrices() {
        fetchProviderPrice(apiEndpoint: "drogasil", price: $drogasilPrice)
        fetchProviderPrice(apiEndpoint: "globo", price: $globoPrice)
        fetchProviderPrice(apiEndpoint: "paguemenos", price: $pagueMenosPrice)
        fetchProviderPrice(apiEndpoint: "ifood", price: $ifoodPrice)
    }

    func fetchProviderPrice(apiEndpoint: String, price: Binding<Double?>) {
        let urlString = "http://localhost:8000/api/\(apiEndpoint)/\(medicineName.lowercased())/?cep=\(cep)"
        
        guard let url = URL(string: urlString) else {
            updateLoadingState()
            return
        }
        
        let task = URLSession.shared.dataTask(with: url) { data, response, error in
            DispatchQueue.main.async {
                if let data = data {
                    if let decodedResponse = try? JSONDecoder().decode(PriceResponse.self, from: data) {
                        print("Decoded \(apiEndpoint.capitalized) Response: \(decodedResponse)") // Debug print
                        price.wrappedValue = decodedResponse.lowest_price
                        if !showTable {
                            showTable = true
                        }
                    } else {
                        print("Failed to decode \(apiEndpoint.capitalized) response: \(String(data: data, encoding: .utf8) ?? "No data")") // Debug print
                        price.wrappedValue = nil
                    }
                } else {
                    print("No data received or error for \(apiEndpoint.capitalized): \(error?.localizedDescription ?? "Unknown error")") // Debug print
                    price.wrappedValue = nil
                }
                updateLoadingState()
            }
        }
        task.resume()
    }

    func updateLoadingState() {
        pendingRequests -= 1
        if pendingRequests == 0 {
            isLoading = false
        }
    }

    func sortedPrices() -> [(name: String, price: Double, provider: String)] {
        let providers = [
            ("Drogasil", drogasilPrice, "drogasil"),
            ("Drogaria Globo", globoPrice, "globo"),
            ("Pague Menos", pagueMenosPrice, "paguemenos"),
            ("iFood", ifoodPrice, "ifood")
        ]
        
        return providers
            .compactMap { name, price, provider in
                if let price = price {
                    return (name: name, price: price, provider: provider)
                } else {
                    return nil
                }
            }
            .sorted { $0.price < $1.price }
    }

    func priceRow(name: String, price: Double, provider: String) -> some View {
        HStack {
            Text(name)
                .frame(maxWidth: .infinity, alignment: .leading)
            Text(String(format: "R$ %.2f", price))
                .frame(maxWidth: .infinity, alignment: .leading)
            Button(action: {
                guard let url = URL(string: "https://\(provider).com.br/\(medicineName.lowercased().replacingOccurrences(of: " ", with: "-"))") else { return }
                selectedProviderURL = url
                showSafari = true
            }) {
                Text("Comprar")
                    .padding(8)
                    .background(Color.green)
                    .foregroundColor(.white)
                    .cornerRadius(8)
            }
        }
        .frame(height: 50) // Fixed height for rows
    }
}

struct SafariView: UIViewControllerRepresentable {
    let url: URL

    func makeUIViewController(context: Context) -> SFSafariViewController {
        return SFSafariViewController(url: url)
    }

    func updateUIViewController(_ uiViewController: SFSafariViewController, context: Context) {}
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
