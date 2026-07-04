import { Component } from "react";

export default class ErrorBoundary extends Component {
  state = { error: null };

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error("Unhandled dashboard error:", error, info);
  }

  render() {
    if (this.state.error) {
      return (
        <div className="max-w-md mx-auto mt-16 p-6 text-center">
          <div className="bg-white rounded-lg shadow p-6 flex flex-col gap-3">
            <h2 className="text-xl font-semibold text-slate-800">Something went wrong</h2>
            <p className="text-sm text-slate-500">{this.state.error.message}</p>
            <button
              onClick={() => window.location.reload()}
              className="bg-slate-800 text-white rounded px-3 py-2 hover:bg-slate-700"
            >
              Reload
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
