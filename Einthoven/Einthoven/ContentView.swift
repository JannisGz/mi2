//
//  ContentView.swift
//  Einthoven
//
//  Created by Yannick Börner on 29.03.21.
//

import SwiftUI
import HealthKit

struct ContentView: View {
    
    @State var serverAddress: String = UserDefaultsProvider.getValueFromUserDefaults(key: "serverAddress") ?? ""
    @State var patientReference: String = UserDefaultsProvider.getValueFromUserDefaults(key: "patientReference") ?? ""
    @State private var color_ECG = Color.red
    @State private var color_height = Color.red
    @State private var color_weight = Color.red
    @State var text_ECG = " "
    @State var text_height = " "
    @State var text_weight = " "
    
    var body: some View {
        ScrollView(Axis.Set.vertical, showsIndicators: true) {
            VStack {
                VStack {
                    Image("1-01-transparent-cropped")
                        .resizable()
                        .scaledToFit()
                        .frame(width: 250, height: 250)
                    TextField("FHIR Server Adresse", text: $serverAddress, onCommit: {
                        UserDefaultsProvider.setValueInUserDefaults(key: "serverAddress", value: self.serverAddress)
                    })
                        .multilineTextAlignment(.center)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                    TextField("Patienten Referenz", text: $patientReference, onCommit: {
                        UserDefaultsProvider.setValueInUserDefaults(key: "patientReference", value: self.patientReference)
                    })
                        .multilineTextAlignment(.center)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                Spacer(minLength: 20)
            }.padding()
            Button(action: {
                UserDefaultsProvider.setValueInUserDefaults(key: "serverAddress", value: self.serverAddress)
                UserDefaultsProvider.setValueInUserDefaults(key: "patientReference", value: self.patientReference)
                HKAuthorizer.authorizeHealthKit(completion: { (success, error) in
                    let ecgType = HKObjectType.electrocardiogramType()
                    let anchor = HKAnchorProvider.GetAnchor(forType: ecgType)
                    //let anchor = HKQueryAnchor.init(fromValue: 0)
                   
                    HKSynchronizer().Synchronize(type: ecgType, predicate: nil, anchor: anchor, limit: HKObjectQueryNoLimit) { (success) in
                        if (success.0) {
                            text_ECG = success.1 + " EKG"
                            if (!success.1.contains("1")) {
                                text_ECG.append("s")
                            }
                            if (success.1.contains("Fehler")){
                                color_ECG = Color.red
                            }
                            else if (success.1.contains("Erfolg")){
                                color_ECG = Color.green
                            }
                            else {
                                color_ECG = Color.black
                            }
                            print("All records synchronized")
                        } else {
                            print("There was an error during synchronization")
                        }
                    }
                })
                
            }) {
                Text("EKGs Synchronisieren")
            }.foregroundColor(.white)
            .padding()
            .background(Color.accentColor)
            .cornerRadius(8)
            
            VStack{
                Text(text_ECG).foregroundColor(color_ECG)
            }
            Spacer(minLength: 10)
            
            Button(action: {
                UserDefaultsProvider.setValueInUserDefaults(key: "serverAddress", value: self.serverAddress)
                UserDefaultsProvider.setValueInUserDefaults(key: "patientReference", value: self.patientReference)
                HKAuthorizer.authorizeHealthKit(completion: { (success, error) in
                    let weightType = HKObjectType.quantityType(forIdentifier: HKQuantityTypeIdentifier.bodyMass)!
                    let weightAnchor = HKAnchorProvider.GetAnchor(forType: weightType)
                    HKSynchronizer().Synchronize(type: weightType, predicate: nil, anchor: weightAnchor, limit: HKObjectQueryNoLimit) { success in
                        if (success.0) {
                            text_weight = success.1 + " Beobachtung"
                            if (!success.1.contains("1")) {
                                text_weight.append("en")
                            }
                            if (success.1.contains("Fehler")){
                                color_weight = Color.red
                            }
                            else if (success.1.contains("Erfolg")){
                                color_weight = Color.green
                            }
                            else {
                                color_weight = Color.black
                            }
                            text_weight = text_weight + " - Körpergewicht"
                            print("All records synchronized")
                        } else {
                            print("There was an error during synchronization")
                        }
                    }
                    
                    let heightType = HKQuantityType.quantityType(forIdentifier: HKQuantityTypeIdentifier.height)!
                    let heightAnchor = HKAnchorProvider.GetAnchor(forType: heightType)
                    HKSynchronizer().Synchronize(type: heightType, predicate: nil, anchor: heightAnchor, limit: HKObjectQueryNoLimit) { (success) in
                        if (success.0) {
                            text_height = success.1 + " Beobachtung"
                            if (!success.1.contains("1")) {
                                text_height.append("en")
                            }
                            if (success.1.contains("Fehler")){
                                color_height = Color.red
                            }
                            else if (success.1.contains("Erfolg")){
                                color_height = Color.green
                            }
                            else {
                                color_height = Color.black
                            }
                            text_height = text_height + " - Körpergröße"
                            print("All records synchronized")
                        } else {
                            print("There was an error during synchronization")
                        }
                    }
                    
                    //let dobType = HKCharacteristicType.characteristicType(forIdentifier: HKCharacteristicTypeIdentifier.dateOfBirth)!
                    //HKSynchronizer().Synchronize(type: dobType, predicate: nil, anchor: anchor, limit: HKObjectQueryNoLimit) { (success) in
                    //    if (success) {
                    //        print("All records synchronized")
                    //    } else {
                    //        print("There was an error during synchronization")
                    //    }
                    //}
                })
                
            }) {
                Text("Größe & Gewicht Synchronisieren")
            }.foregroundColor(.white)
            .padding()
            .background(Color.accentColor)
            .cornerRadius(8)
            
            VStack{
                Spacer(minLength: 10)
                Text(text_weight).foregroundColor(color_weight)
                Text(text_height).foregroundColor(color_height)
            }
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
