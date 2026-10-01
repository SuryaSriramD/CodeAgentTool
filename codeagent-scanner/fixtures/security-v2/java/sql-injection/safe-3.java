import java.sql.*;
import javax.xml.parsers.*;
class Example { void handle(Statement stmt, String input, DocumentBuilderFactory factory) { String sql = "SELECT * FROM users WHERE name=" + input; System.out.println(sql); } }
