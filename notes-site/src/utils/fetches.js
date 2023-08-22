// look for and load the .env file
import dotenv from "dotenv";
dotenv.config();

// set the baseURL variable to the value of the BASE_URL environment variable
const baseURL = process.env.BASE_URL;

console.log("baseURL: ", baseURL);
