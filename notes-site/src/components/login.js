export default function LoginPage() {
  return (
    <div className="container mx-auto bg-gray-300 rounded-xl shadow border p-8 m-10 max-w-2xl">
      <p className="text-3xl text-gray-700 font-bold mb-5">Login</p>

      <form className="flex flex-col px-4" action="/login" method="POST">
        <label className="text-gray-700 text-lg mb-2" htmlFor="username">
          Username
        </label>
        <input
          className="border border-gray-400 p-2 mb-4"
          type="text"
          name="username"
          id="username"
        />

        <label className="text-gray-700 text-lg mb-2" htmlFor="password">
          Password
        </label>
        <input
          className="border border-gray-400 p-2 mb-4"
          type="password"
          name="password"
          id="password"
        />

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
