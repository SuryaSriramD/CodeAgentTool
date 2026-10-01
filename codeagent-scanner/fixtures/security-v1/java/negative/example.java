import java.security.MessageDigest;
class Example { void run() { try { MessageDigest.getInstance("SHA-256"); } catch (java.security.NoSuchAlgorithmException e) { System.err.println(e); } } }
