import SwiftUI

// Define models for both success and error responses
struct PriceResponse: Codable {
    let id: Int
    let name: String
    let prices: [Price]
    
    struct Price: Codable, Identifiable {
        let id: Int
        let provider: String
        let price: String
        let medicine: Int
    }
}

struct ErrorResponse: Codable {
    let error: String
}

struct ContentView: View {
    @State private var medicineName: String = ""
    @State private var prices: [String] = []
    @State private var isLoading: Bool = false
    @State private var isAvailable: Bool = true // Track availability

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

                if isLoading {
                    ProgressView()
                        .padding()
                }

                List(prices, id: \.self) { price in
                    HStack {
                        Text(price)
                        Spacer()
                        if isAvailable {
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
            }
            .padding()
            .navigationTitle("MedScan")
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarItems(leading: EmptyView(), trailing: EmptyView()) // To center the title
        }
    }

    func fetchPrices() {
        isLoading = true

        // Replace with your actual API URL
        let urlString = "http://localhost:8000/api/medicines/\(medicineName.lowercased())/prices/"
        guard let url = URL(string: urlString) else {
            isLoading = false
            return
        }
        
        let task = URLSession.shared.dataTask(with: url) { data, response, error in
            if let error = error {
                print("Error fetching data: \(error)")
                DispatchQueue.main.async {
                    self.isLoading = false
                    self.prices = ["Error fetching data"]
                    self.isAvailable = false
                }
                return
            }
            
            guard let data = data else {
                DispatchQueue.main.async {
                    self.isLoading = false
                    self.prices = ["No data received"]
                    self.isAvailable = false
                }
                return
            }
            
            // Print the raw JSON data for debugging
            if let jsonString = String(data: data, encoding: .utf8) {
                print("Raw JSON response: \(jsonString)")
            }
            
            do {
                // Attempt to decode as PriceResponse
                self.isLoading = false
                let decodedResponse = try JSONDecoder().decode(PriceResponse.self, from: data)
                DispatchQueue.main.async {
                    if decodedResponse.prices.isEmpty {
                        self.prices = ["Sorry, this medicine is not available in our Database"]
                        self.isAvailable = false
                    } else {
                        self.prices = decodedResponse.prices.map { "\($0.provider): R$ \($0.price)" }
                        self.isAvailable = true
                    }
                }
            } catch {
                self.prices = ["Sorry, this medicine is not available in our Database"]
                self.isAvailable = false
            }
        }
        
        task.resume()
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
