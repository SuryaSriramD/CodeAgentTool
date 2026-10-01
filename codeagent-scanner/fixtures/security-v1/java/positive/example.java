import java.security.MessageDigest;
class Example { void run() { try { MessageDigest.getInstance("MD5"); } catch (java.security.NoSuchAlgorithmException e) { System.err.println(e); } } }
