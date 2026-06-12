declare const _default: {
    content: string[];
    theme: {
        extend: {
            animation: {
                "pulse-slow": string;
                "fade-in-up": string;
                "fade-in": string;
                "slide-in-right": string;
            };
            keyframes: {
                fadeIn: {
                    from: {
                        opacity: string;
                    };
                    to: {
                        opacity: string;
                    };
                };
                fadeInUp: {
                    from: {
                        opacity: string;
                        transform: string;
                    };
                    to: {
                        opacity: string;
                        transform: string;
                    };
                };
                slideInRight: {
                    from: {
                        opacity: string;
                        transform: string;
                    };
                    to: {
                        opacity: string;
                        transform: string;
                    };
                };
            };
        };
    };
    plugins: any[];
};
export default _default;
