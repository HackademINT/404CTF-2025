use dotenv::dotenv;
use rocket::{Config, fs::NamedFile};
use rocket_dyn_templates::Template;
use std::{
    env,
    path::{Path, PathBuf},
};

mod insecurity;
mod pages;
mod security;

#[macro_use]
extern crate rocket;

#[get("/<file..>")]
async fn static_files(file: PathBuf) -> Option<NamedFile> {
    NamedFile::open(
        Path::new(
            &env::var("STATIC_PATH").expect("STATIC_PATH must be set (should be in ./.env)."),
        )
        .join(file),
    )
    .await
    .ok()
}

#[launch]
async fn rocket() -> _ {
    dotenv().ok();

    rocket::build()
        .mount("/", routes![pages::index, pages::flag, pages::test,])
        .mount("/static", routes![static_files])
        .attach(Template::fairing())
        .configure(Config {
            log_level: rocket::config::LogLevel::Off,
            ..Default::default()
        })
}
