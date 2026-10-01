fn handle(input: &str, connection: rusqlite::Connection) {
sqlx::query(&format!("SELECT * FROM users WHERE name={}",input));
}
