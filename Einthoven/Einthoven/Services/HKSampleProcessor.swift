//
//  HKSampleProcessor.swift
//  Einthoven
//
//  Created by Yannick Börner on 29.03.21.
//

import Foundation
import HealthKit
import FHIR

class HKSampleProcessor {
    var client: FhirClient
    var dispatchGroup: DispatchGroup
    var processingDispatchGroup: DispatchGroup
    var resources: [Resource]
    private let accessQueue = DispatchQueue(label: "SynchronizedArrayAccess", attributes: .concurrent)
    
    init(client: FhirClient) {
        self.client = client
        self.dispatchGroup = DispatchGroup()
        self.processingDispatchGroup = DispatchGroup()
        self.resources = [Resource]()
    }
    
    func ProcessResults(samples: [HKSample], closure: @escaping (_ result: Bool) -> Void) {
        print("Create batch bundle(s) with observations")
        
        for sample in samples {
            self.processingDispatchGroup.enter()
            
            print(sample.sampleType)
            
            if (sample.sampleType == HKObjectType.electrocardiogramType()){
            
                let ecgSample = sample as! HKElectrocardiogram
                
                HKEcgVoltageProvider().GetMeasurementsForHKElectrocardiogram(sample: ecgSample) { (measurements) in
                    let observation = self.CreateObservationECG(measurements: measurements)
                    
                    self.accessQueue.async(flags:.barrier) {
                        self.resources.append(observation)
                        self.processingDispatchGroup.leave()
                    }
                }
            }
            if (sample.sampleType == HKObjectType.quantityType(forIdentifier: HKQuantityTypeIdentifier.bodyMass)){
                let content = sample.description.split(separator: " ")
                let observation = self.CreateObservationQuantity(value: String(content[0]), unit: String(content[1]), t: "bodyMass")
                self.accessQueue.async(flags:.barrier) {
                    self.resources.append(observation)
                    self.processingDispatchGroup.leave()
                }
                
            }
            if (sample.sampleType == HKObjectType.quantityType(forIdentifier: HKQuantityTypeIdentifier.height)){
                let content = sample.description.split(separator: " ")
                let observation = self.CreateObservationQuantity(value: String(content[0]), unit: String(content[1]), t: "height")
                self.accessQueue.async(flags:.barrier) {
                    self.resources.append(observation)
                    self.processingDispatchGroup.leave()
                }
                
            }
        }
        
        self.processingDispatchGroup.notify(queue: .main) {
            if (self.resources.count > 0) {
                self.SendResources(resources: self.resources)
            }
            self.dispatchGroup.notify(queue: .main) {
                print("HKSampleProcessor - All results have been processed")
                closure(false)
            }
        }
    }
    
    private func CreateObservationECG(measurements: String) -> Observation {
        let observation = TemplateProvider.GetObservationTemplate(t: "ECG")
        observation.component?.first?.valueSampledData?.data = FHIRString(measurements)
        
        var reference = "Patient/"
        let referenceValue = UserDefaultsProvider.getValueFromUserDefaults(key: "patientReference")
        if (referenceValue != nil) {
            reference += referenceValue!
        }
        observation.subject?.reference = FHIRString(reference)
        return observation
    }
    
    private func CreateObservationQuantity(value: String, unit: String, t: String) -> Observation {
        let observation = TemplateProvider.GetObservationTemplate(t: t)
        observation.valueQuantity?.value = FHIRDecimal(value)
        observation.valueQuantity?.unit = FHIRString(unit)
        
        var reference = "Patient/"
        let referenceValue = UserDefaultsProvider.getValueFromUserDefaults(key: "patientReference")
        if (referenceValue != nil) {
            reference += referenceValue!
        }
        observation.subject?.reference = FHIRString(reference)
        return observation
    }
    
    private func SendResources(resources: [Resource]) {
        print("HKSampleProcessor - Attempting to transmit bundle with \(resources.count) entries")
        
        for r in resources {
            client.send(resource: r){( success: Bool) in
                print(r.id)
            }
        }
        
        
        //let bundle = TransactionBundle(resources: resources).bundle
        //print(bundle.entry)
        
        //dispatchGroup.enter()
        //client.send(resource: bundle) {( success: Bool) in
        //    self.dispatchGroup.leave()
        //}
    }
}
