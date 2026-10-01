import java.sql.*;
import javax.xml.parsers.*;
class Example { void handle(Statement stmt, String input, DocumentBuilderFactory factory) { stmt.execute("SELECT * FROM users ORDER BY " + input); } }
