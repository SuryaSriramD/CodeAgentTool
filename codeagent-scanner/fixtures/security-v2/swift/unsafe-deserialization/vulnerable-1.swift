import Foundation
import Alamofire
func handler(data: Data, trust: SecTrust, challenge: URLAuthenticationChallenge) {
let value = NSKeyedUnarchiver.unarchiveObject(with: data)
}
