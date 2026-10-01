import java.sql.Statement
import javax.xml.parsers.DocumentBuilderFactory
fun handle(stmt: Statement, input: String, factory: DocumentBuilderFactory) {
println("SELECT * FROM users WHERE name=" + input)
}
