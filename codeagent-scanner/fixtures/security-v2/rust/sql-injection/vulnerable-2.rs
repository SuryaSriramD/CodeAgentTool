fn handle(input: &str, connection: rusqlite::Connection) {
connection.execute(&format!("DELETE FROM users WHERE id={}",input), []);
}
