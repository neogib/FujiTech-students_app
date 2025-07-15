// @ts-check
import withNuxt from "./.nuxt/eslint.config.mjs";
import eslintConfigPrettier from "eslint-config-prettier/flat";

export default withNuxt({
	rules: {
		"no-else-return": 2,
	},
}).append(eslintConfigPrettier);
