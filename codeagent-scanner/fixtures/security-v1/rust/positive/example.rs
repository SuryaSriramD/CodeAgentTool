fn run(input: &str) { std::process::Command::new("sh").arg("-c").arg(input).status(); }
