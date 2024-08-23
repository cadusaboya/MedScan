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
    @State private var isLoadingDrogasil: Bool = false
    @State private var isLoadingGlobo: Bool = false
    @State private var isLoadingPagueMenos: Bool = false
    @State private var isLoadingIFood: Bool = false
    @State private var selectedProviderURL: URL?
    @State private var showSafari: Bool = false

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
                    fetchPrices()
                }) {
                    Text("Search")
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.black)
                        .foregroundColor(.white)
                        .cornerRadius(8)
                }
                .padding()

                List {
                    HStack {
                        Text("Fornecedor")
                            .frame(width: 150, alignment: .leading) // Fixed width for provider names
                            .fontWeight(.bold)
                        Text("Price")
                            .frame(width: 100, alignment: .leading) // Fixed width for prices
                            .fontWeight(.bold)
                        Text("") // Empty space for button
                            .frame(width: 80, alignment: .leading) // Fixed width for button space
                    }
                    .frame(height: 50) // Fixed height for header row

                    priceRow(name: "Drogasil", price: drogasilPrice, isLoading: isLoadingDrogasil, provider: "drogasil")
                    priceRow(name: "Drogaria Globo", price: globoPrice, isLoading: isLoadingGlobo, provider: "globo")
                    priceRow(name: "Pague Menos", price: pagueMenosPrice, isLoading: isLoadingPagueMenos, provider: "paguemenos")
                    priceRow(name: "iFood", price: ifoodPrice, isLoading: isLoadingIFood, provider: "ifood")
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

    func fetchPrices() {
        fetchProviderPrice(apiEndpoint: "drogasil", isLoading: $isLoadingDrogasil, price: $drogasilPrice)
        fetchProviderPrice(apiEndpoint: "globo", isLoading: $isLoadingGlobo, price: $globoPrice)
        fetchProviderPrice(apiEndpoint: "paguemenos", isLoading: $isLoadingPagueMenos, price: $pagueMenosPrice)
        fetchProviderPrice(apiEndpoint: "ifood", isLoading: $isLoadingIFood, price: $ifoodPrice)
    }

    func fetchProviderPrice(apiEndpoint: String, isLoading: Binding<Bool>, price: Binding<Double?>) {
        isLoading.wrappedValue = true
        let urlString = "http://localhost:8000/api/\(apiEndpoint)/\(medicineName.lowercased())/?cep=\(cep)"
        
        guard let url = URL(string: urlString) else {
            isLoading.wrappedValue = false
            return
        }
        
        let task = URLSession.shared.dataTask(with: url) { data, response, error in
            DispatchQueue.main.async {
                isLoading.wrappedValue = false
                if let data = data {
                    if let decodedResponse = try? JSONDecoder().decode(PriceResponse.self, from: data) {
                        print("Decoded \(apiEndpoint.capitalized) Response: \(decodedResponse)") // Debug print
                        price.wrappedValue = decodedResponse.lowest_price
                    } else {
                        print("Failed to decode \(apiEndpoint.capitalized) response: \(String(data: data, encoding: .utf8) ?? "No data")") // Debug print
                        price.wrappedValue = nil
                    }
                } else {
                    print("No data received or error for \(apiEndpoint.capitalized): \(error?.localizedDescription ?? "Unknown error")") // Debug print
                    price.wrappedValue = nil
                }
            }
        }
        task.resume()
    }

    func priceRow(name: String, price: Double?, isLoading: Bool, provider: String) -> some View {
        HStack {
            Text(name)
                .frame(width: 150, alignment: .leading) // Fixed width for provider names
            if isLoading {
                ProgressView()
                    .frame(width: 100, alignment: .leading) // Fixed width for loading indicator
            } else if let price = price {
                Text(String(format: "R$ %.2f", price))
                    .frame(width: 100, alignment: .leading) // Fixed width for price
                Button(action: {
                    guard let url = URL(string: "https://\(provider).com.br/\(medicineName.lowercased().replacingOccurrences(of: " ", with: "-"))") else { return }
                    selectedProviderURL = url
                    showSafari = true
                }) {
                    Text("Buy")
                        .frame(width: 80, height: 40)
                        .background(Color.green)
                        .foregroundColor(.white)
                        .cornerRadius(8)
                }
            } else {
                Text("N/A")
                    .frame(width: 100, alignment: .leading) // Fixed width for N/A
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
