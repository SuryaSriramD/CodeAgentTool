import java.sql.Statement
import javax.xml.parsers.DocumentBuilderFactory
fun handle(stmt: Statement, input: String, factory: DocumentBuilderFactory) {
stmt.execute("SELECT * FROM users ORDER BY " + input)
}
