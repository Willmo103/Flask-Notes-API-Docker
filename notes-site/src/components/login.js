export default function LoginPage() {
  return (
    <div className="container mx-auto bg-gray-300 dark:bg-black rounded-xl shadow border p-8 m-10 max-w-2xl">
      <p className="text-3xl text-gray-700 dark:text-gray-300 font-bold mb-5">
        Login
      </p>

      <form className="flex flex-col px-4" action="/login" method="POST">
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
