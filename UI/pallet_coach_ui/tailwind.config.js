export default {
    content: ["./index.html", "./src/**/*.{ts,tsx}"],
    theme: {
        extend: {
            animation: {
                "pulse-slow": "pulse 3s ease-in-out infinite",
                "fade-in-up": "fadeInUp 400ms cubic-bezier(0.16, 1, 0.3, 1) both",
                "fade-in": "fadeIn 320ms ease both",
                "slide-in-right": "slideInRight 380ms cubic-bezier(0.16, 1, 0.3, 1) both",
            },
            keyframes: {
                fadeIn: {
                    from: { opacity: "0" },
                    to: { opacity: "1" },
                },
                fadeInUp: {
                    from: { opacity: "0", transform: "translateY(8px)" },
                    to: { opacity: "1", transform: "translateY(0)" },
                },
                slideInRight: {
                    from: { opacity: "0", transform: "translateX(14px)" },
                    to: { opacity: "1", transform: "translateX(0)" },
                },
            },
        },
    },
    plugins: [require("@tailwindcss/typography")],
};
