import Foundation
import Alamofire
func handler(data: Data, trust: SecTrust, challenge: URLAuthenticationChallenge) {
let evaluator = DisabledTrustEvaluator()
}
