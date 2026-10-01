import Foundation
import Alamofire
func handler(data: Data, trust: SecTrust, challenge: URLAuthenticationChallenge) {
let value = JSONDecoder().decode(String.self, from: data)
}
