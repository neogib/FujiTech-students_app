// @ts-check
import withNuxt from "./.nuxt/eslint.config.mjs";
import eslintConfigPrettier from "eslint-config-prettier/flat";

export default withNuxt({
    ignores: [
        "**/node_modules/**",
        "**/.nuxt/**",
        "**/.output/**",
        "**/dist/**",
        "**/coverage/**",
        "**/.husky/**",
        "**/.vscode/**",
        "**/.idea/**",
        "**/.DS_Store",
        "**/pnpm-lock.yaml",
    ],
    rules: {
        "no-else-return": 2,
    },
}).append(eslintConfigPrettier);
