//
//  EcgObservationTemplateProvider.swift
//  Einthoven
//
//  Created by Yannick Börner on 04.04.21.
//

import Foundation
import FHIR

class TemplateProvider {
    static private var ecgObservationTemplate = GetTemplate(t: "ObservationTemplate")!
    static private var bodyMassObservationTemplate = GetTemplate(t: "bodyMassTemplate")!
    static private var heightObservationTemplate = GetTemplate(t: "heightTemplate")!
    
    static private func GetTemplate(t: String) -> FHIRJSON? {
        if let path = Bundle.main.path(forResource: "FhirTemplates", ofType: "json") {
            do {
                  let data = try Data(contentsOf: URL(fileURLWithPath: path), options: .alwaysMapped)
                  let jsonResult = try JSONSerialization.jsonObject(with: data, options: .mutableLeaves)
                  if let jsonResult = jsonResult as? FHIRJSON, let observationTemplate = jsonResult[t] as? FHIRJSON {
                    return observationTemplate
                  }
              } catch {
                   print(error)
              }
        }
        return nil
    }
    
    static func GetObservationTemplate(t: String) -> Observation {
        do {
            switch t {
            case "ECG":
                let observation = try Observation(json: self.ecgObservationTemplate)
                return observation
            case "bodyMass":
                let observation = try Observation(json: self.bodyMassObservationTemplate)
                return observation
            case "height":
                let observation = try Observation(json: self.heightObservationTemplate)
                return observation
            default:
                return Observation()
            }

        } catch {
            print(error)
            return Observation()
        }
    }
}
