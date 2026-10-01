import Foundation
import Alamofire
func handler(data: Data, trust: SecTrust, challenge: URLAuthenticationChallenge) {
let value = NSKeyedUnarchiver.unarchivedObject(ofClass: NSString.self, from: data)
}
