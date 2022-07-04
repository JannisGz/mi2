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
    
    var body: some View {
        ScrollView(Axis.Set.vertical, showsIndicators: true) {
            VStack {
                VStack {
                    Image("1-01-transparent-cropped")
                        .resizable()
                        .scaledToFit()
                        .frame(width: 250, height: 250)
                    TextField("Server address", text: $serverAddress, onCommit: {
                        UserDefaultsProvider.setValueInUserDefaults(key: "serverAddress", value: self.serverAddress)
                    })
                        .multilineTextAlignment(.center)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                    TextField("Patient reference", text: $patientReference, onCommit: {
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
                        if (success) {
                            print("All records synchronized")
                        } else {
                            print("There was an error during synchronization")
                        }
                    }
                })
                
            }) {
                Text("Synchronize ECG records")
            }.foregroundColor(.white)
            .padding()
            .background(Color.accentColor)
            .cornerRadius(8)
            
            Button(action: {
                UserDefaultsProvider.setValueInUserDefaults(key: "serverAddress", value: self.serverAddress)
                UserDefaultsProvider.setValueInUserDefaults(key: "patientReference", value: self.patientReference)
                HKAuthorizer.authorizeHealthKit(completion: { (success, error) in
                    let weightType = HKObjectType.quantityType(forIdentifier: HKQuantityTypeIdentifier.bodyMass)!
                    let weightAnchor = HKAnchorProvider.GetAnchor(forType: weightType)
                    HKSynchronizer().Synchronize(type: weightType, predicate: nil, anchor: weightAnchor, limit: HKObjectQueryNoLimit) { (success) in
                        if (success) {
                            print("All records synchronized")
                        } else {
                            print("There was an error during synchronization")
                        }
                    }
                    
                    let heightType = HKQuantityType.quantityType(forIdentifier: HKQuantityTypeIdentifier.height)!
                    let heightAnchor = HKAnchorProvider.GetAnchor(forType: heightType)
                    HKSynchronizer().Synchronize(type: heightType, predicate: nil, anchor: heightAnchor, limit: HKObjectQueryNoLimit) { (success) in
                        if (success) {
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
                Text("Synchronize Patient Data")
            }.foregroundColor(.white)
            .padding()
            .background(Color.accentColor)
            .cornerRadius(8)
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
