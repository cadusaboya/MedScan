import SwiftUI
import SafariServices

struct PriceResponse: Codable {
    let name: String
    let lowest_price: Double
    let url: String? // Include this to handle the URL in the response
}

struct BuscadorView: View {
    @State private var medicineName: String = ""
    @State private var cep: String = ""
    @State private var drogasilPriceResponse: PriceResponse?
    @State private var globoPriceResponse: PriceResponse?
    @State private var pagueMenosPriceResponse: PriceResponse?
    @State private var ifoodPriceResponse: PriceResponse?
    @State private var isLoading: Bool = false
    @State private var showTable: Bool = false
    @State private var selectedProviderURL: URL?
    @State private var showSafari: Bool = false
    @State private var pendingRequests: Int = 0

    var body: some View {
            VStack {
                Text("Buscador de Preço")
                    .font(.title)
                    .fontWeight(.bold)
                    .padding(.vertical, 10.0)

                Form {
                    Section(header: Text("Informações")) {
                        TextField("Nome do remédio", text: $medicineName)
                        TextField("Cidade", text: $cep)
                    }
                }
                .frame(height: 130.0)

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
                    ScrollView {
                        VStack(spacing: 16) {
                            ForEach(sortedPrices(), id: \.name) { provider in
                                CardView(name: provider.name, price: provider.price, productName: provider.productName, provider: provider.provider, url: provider.url) { url in
                                    selectedProviderURL = url
                                    showSafari = true
                                }
                            }
                        }
                        .padding()
                    }
                }

                if isLoading {
                    VStack {
                        ProgressView()
                        Text("Buscando preços...")
                            .padding(.top, 10)
                    }
                }

                Spacer()
            }
            .padding()
            .navigationTitle("MedScan")
            .background(Color(UIColor.systemGroupedBackground))
            .navigationBarTitleDisplayMode(.inline)
            .sheet(isPresented: $showSafari) {
                if let url = selectedProviderURL {
                    SafariView(url: url)
                }
            }
        }


    func resetValues() {
        drogasilPriceResponse = nil
        globoPriceResponse = nil
        pagueMenosPriceResponse = nil
        ifoodPriceResponse = nil
    }

    func fetchPrices() {
        fetchProviderPrice(apiEndpoint: "drogasil", priceResponse: $drogasilPriceResponse)
        fetchProviderPrice(apiEndpoint: "globo", priceResponse: $globoPriceResponse)
        fetchProviderPrice(apiEndpoint: "paguemenos", priceResponse: $pagueMenosPriceResponse)
        fetchProviderPrice(apiEndpoint: "ifood", priceResponse: $ifoodPriceResponse)
    }

    func fetchProviderPrice(apiEndpoint: String, priceResponse: Binding<PriceResponse?>) {
        let urlString = "http://localhost:8000/api/\(apiEndpoint)/\(medicineName.lowercased())/?cep=\(cep)"
        
        guard let url = URL(string: urlString) else {
            updateLoadingState()
            return
        }
        
        let configuration = URLSessionConfiguration.default
        configuration.timeoutIntervalForRequest = 60.0
        
        let session = URLSession(configuration: configuration)
        
        let task = session.dataTask(with: url) { data, response, error in
            DispatchQueue.main.async {
                if let data = data {
                    if let decodedResponse = try? JSONDecoder().decode(PriceResponse.self, from: data) {
                        print("Decoded \(apiEndpoint.capitalized) Response: \(decodedResponse)") // Debug print
                        priceResponse.wrappedValue = decodedResponse
                        if !showTable {
                            showTable = true
                        }
                    } else {
                        print("Failed to decode \(apiEndpoint.capitalized) response: \(String(data: data, encoding: .utf8) ?? "No data")") // Debug print
                        priceResponse.wrappedValue = nil
                    }
                } else {
                    print("No data received or error for \(apiEndpoint.capitalized): \(error?.localizedDescription ?? "Unknown error")") // Debug print
                    priceResponse.wrappedValue = nil
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

    func sortedPrices() -> [(name: String, price: Double, productName: String, provider: String, url: URL?)] {
        let providers = [
            ("Drogasil", drogasilPriceResponse, "drogasil"),
            ("Drogaria Globo", globoPriceResponse, "globo"),
            ("Pague Menos", pagueMenosPriceResponse, "paguemenos"),
            ("iFood", ifoodPriceResponse, "ifood")
        ]
        
        return providers
            .compactMap { name, priceResponse, provider in
                if let response = priceResponse {
                    let url = URL(string: response.url ?? "")
                    return (name: name, price: response.lowest_price, productName: response.name, provider: provider, url: url)
                } else {
                    return nil
                }
            }
            .sorted { $0.price < $1.price }
    }
}

struct CardView: View {
    let name: String
    let price: Double
    let productName: String
    let provider: String
    let url: URL?
    let action: (URL?) -> Void

    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 8) {
                Text(name)
                    .font(.headline)
                    .lineLimit(1)
                
                Text(productName)
                    .font(.subheadline)
                    .lineLimit(5)
                
                Text(String(format: "R$ %.2f", price))
                    .font(.subheadline)
                    .foregroundColor(.green)
            }
            .padding()
            
            Spacer()
            
            Button(action: {
                action(url)
            }) {
                Text("Comprar")
                    .font(.subheadline)
                    .padding()
                    .background(Color.green)
                    .foregroundColor(.white)
                    .cornerRadius(8)
            }
        }
        .padding(.horizontal)
        .frame(maxWidth: .infinity)
        .background(Color.white)
        .cornerRadius(10)
        .shadow(radius: 5)
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
        BuscadorView()
    }
}
