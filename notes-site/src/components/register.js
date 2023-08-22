const url = process.env.BASE_URL + "/api/register";

export default function RegisterPage() {
  return (
    <div className="container mx-auto bg-gray-300 dark:bg-black rounded-xl shadow border p-8 m-10 max-w-2xl">
      <p className="text-3xl text-gray-700 dark:text-gray-300 font-bold mb-5">
        Sign Up
      </p>

      <form
        className="flex flex-col px-4"
        action="/login"
        method="POST"
        onSubmit={(e) => {
          e.preventDefault();
          const username = e.target.username.value;
          const email = e.target.email.value;
          const password = e.target.password.value;
          const confirm_password = e.target.confirm_password.value;
          if (password !== confirm_password) {
            alert("Passwords do not match!");
            // use a react popup to display the error message
            // https://www.npmjs.com/package/reactjs-popup
          } else {
            const data = {
              username,
              email,
              password,
            };
            const options = {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify(data),
            };
            fetch(url, options)
              .then((res) => res.json())
              .then((data) => {
                if (data.error) {
                  alert(data.error);
                } else {
                  alert("User created!");
                }
              })
              .catch((err) => {
                console.log(err);
                alert("Error!");
              });
          }
          return;
        }} // end of onSubmit
      >
        <label
          className="text-gray-700 dark:text-gray-300 text-lg mb-2"
          htmlFor="username"
        >
          Username
        </label>
        <input
          className="border border-gray-400 p-2 mb-4 dark:bg-gray-700 dark:text-gray-300"
          placeholder="username"
          type="text"
          name="username"
          id="username"
        />

        <label
          className="text-gray-700 dark:text-gray-300 text-lg mb-2"
          htmlFor="email"
        >
          Email
        </label>
        <input
          className="border border-gray-400 p-2 mb-4 dark:bg-gray-700 dark:text-gray-300"
          placeholder="user@email.com"
          type="email"
          name="email"
          id="email"
        />

        <label
          className="text-gray-700 dark:text-gray-300 text-lg mb-2"
          htmlFor="password"
        >
          Password
        </label>
        <input
          className="border border-gray-400 p-2 mb-4 dark:bg-gray-700 dark:text-gray-300"
          placeholder="password"
          type="password"
          name="password"
          id="password"
        />
        <label
          className="text-gray-700 dark:text-gray-300 text-lg mb-2"
          htmlFor="confirm_password"
        >
          Confirm Password
        </label>
        <input
          className="border border-gray-400 p-2 mb-4 dark:bg-gray-700 dark:text-gray-300"
          placeholder="confirm password"
          type="password"
          name="confirm_password"
          id="confirm_password"
        />
        <label
          className="text-gray-700 dark:text-gray-300 text-lg mb-2"
          htmlFor="remember_me"
        >
          Remember Me
        </label>
        <div className="flex justify-start">
          <input
            type="checkbox"
            name="remember_me"
            id="remember_me"
            className="mb-4 "
          />
        </div>
        <button
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          type="submit"
        >
          Login
        </button>
      </form>
    </div>
  );
}
