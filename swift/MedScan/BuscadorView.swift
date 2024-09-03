import SwiftUI
import SafariServices

struct PriceResponse: Codable {
    let name: String
    let price: Double
    let url: String
}

struct BuscadorView: View {
    @State private var medicineName: String = ""
    @State private var cep: String = ""
    @State private var drogasilPriceResponses: [PriceResponse] = []
    @State private var globoPriceResponses: [PriceResponse] = []
    @State private var pagueMenosPriceResponses: [PriceResponse] = []
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
                pendingRequests = 3 // Number of providers
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
                        ForEach(sortedPrices(), id: \.name) { item in
                            CardView(name: item.provider, price: item.price, productName: item.name, provider: item.provider, url: item.url) { url in
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
        drogasilPriceResponses = []
        globoPriceResponses = []
        pagueMenosPriceResponses = []
    }

    func fetchPrices() {
        fetchProviderPrice(apiEndpoint: "drogasil", priceResponses: $drogasilPriceResponses)
        fetchProviderPrice(apiEndpoint: "globo", priceResponses: $globoPriceResponses)
        fetchProviderPrice(apiEndpoint: "paguemenos", priceResponses: $pagueMenosPriceResponses)
    }

    func fetchProviderPrice(apiEndpoint: String, priceResponses: Binding<[PriceResponse]>) {
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
                    if let decodedResponses = try? JSONDecoder().decode([PriceResponse].self, from: data) {
                        print("Decoded \(apiEndpoint.capitalized) Responses: \(decodedResponses)") // Debug print
                        priceResponses.wrappedValue = decodedResponses
                        if !showTable {
                            showTable = true
                        }
                    } else {
                        print("Failed to decode \(apiEndpoint.capitalized) responses: \(String(data: data, encoding: .utf8) ?? "No data")") // Debug print
                        priceResponses.wrappedValue = []
                    }
                } else {
                    print("No data received or error for \(apiEndpoint.capitalized): \(error?.localizedDescription ?? "Unknown error")") // Debug print
                    priceResponses.wrappedValue = []
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

    func sortedPrices() -> [(name: String, price: Double, provider: String, url: URL?)] {
        var allPrices: [(name: String, price: Double, provider: String, url: URL?)] = []
        
        let providers: [(String, [PriceResponse])] = [
            ("Drogasil", drogasilPriceResponses),
            ("Drogaria Globo", globoPriceResponses),
            ("Pague Menos", pagueMenosPriceResponses)
        ]
        
        for (providerName, responses) in providers {
            for response in responses {
                if let url = URL(string: response.url) {
                    allPrices.append((name: response.name, price: response.price, provider: providerName, url: url))
                }
            }
        }
        
        return allPrices.sorted { $0.price < $1.price }
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
