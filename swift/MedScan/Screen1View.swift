import SwiftUI

struct MainPageView: View {
    var body: some View {
            VStack(alignment: .leading, spacing: 20) {
                
                // App Info Section
                VStack(alignment: .leading, spacing: 10) {
                    Text("Quem somos?")
                        .font(.title2)
                        .fontWeight(.semibold)
                    
                    
                    Text("MedScan é uma inteligência artificial a sua disposição para lhe ajudar a economizar na compra de medicamentos.")
                        .font(.body)
                        .foregroundColor(.gray)
                }
                .padding(.vertical, 30)
                .padding(.horizontal)
                
                // Features Section
                VStack(alignment: .leading, spacing: 20) {
                    Text("Funcionalidades")
                        .font(.title2)
                        .fontWeight(.semibold)
                    
                    VStack(alignment: .leading, spacing: 8) {
                        FeatureView(icon: "magnifyingglass", title: "Buscador de Preço", description: "Procure um medicamento nas farmácias mais populares do Brasil")
                        FeatureView(icon: "location", title: "Em breve: Buscador de similares", description: "Receba a partir de um nome todos os genéricos e similares do medicamento")
                        FeatureView(icon: "checkmark.seal", title: "Em breve: Leitor de Receita", description: "Deixe nossa IA ler a sua receita e encontrar todos os medicamentos no melhor preço utilizando as funcionalidades acima")
                    }
                }
                .padding(.horizontal)
                
                Spacer()
                
                // Contact Section
                VStack(alignment: .leading, spacing: 10) {
                    Text("Fale Conosco")
                        .font(.title2)
                        .fontWeight(.semibold)
                    
                    Text("Tem alguma pergunta ou precisa de suporte? Entre em contato em:")
                        .font(.body)
                        .foregroundColor(.gray)
                    
                    Text("medscan@gmail.com")
                        .font(.body)
                        .foregroundColor(.blue)
                }
                .padding(.horizontal)
                .padding(.bottom, 40)
            }
            .padding(.horizontal)
            .background(Color(UIColor.systemGroupedBackground))
            .navigationTitle("MedScan")
            .navigationBarTitleDisplayMode(.inline)
        }
    }

struct FeatureView: View {
    let icon: String
    let title: String
    let description: String
    
    var body: some View {
        HStack(alignment: .top) {
            Image(systemName: icon)
                .foregroundColor(.blue)
                .frame(width: 30, height: 30)
            
            VStack(alignment: .leading) {
                Text(title)
                    .font(.headline)
                    .fontWeight(.medium)
                
                Text(description)
                    .font(.subheadline)
                    .foregroundColor(.gray)
            }
        }
    }
}

struct MainPageView_Previews: PreviewProvider {
    static var previews: some View {
        MainPageView()
    }
}
