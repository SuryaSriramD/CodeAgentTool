import CommonCrypto
func run(_ data: UnsafeRawPointer, _ digest: UnsafeMutablePointer<UInt8>) { CC_MD5(data, 8, digest) }
