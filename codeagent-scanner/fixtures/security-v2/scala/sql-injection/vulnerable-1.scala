import java.sql.Statement
import javax.xml.parsers.DocumentBuilderFactory
object Example { def handle(stmt: Statement, input: String, factory: DocumentBuilderFactory): Unit = {
stmt.executeQuery("SELECT * FROM users WHERE name=" + input)
} }
