import java.sql.*;
import javax.xml.parsers.*;
class Example { void handle(Statement stmt, String input, DocumentBuilderFactory factory) { stmt.executeUpdate("DELETE FROM users WHERE id=42"); } }
