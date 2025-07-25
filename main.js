import { AutoTokenizer, AutoModelForCausalLM } from '@xenova/transformers';
import { generateStegoText } from './stego_generator.js';

async function main() {
  const modelName = 'gpt2';
  const tokenizer = await AutoTokenizer.from_pretrained(modelName);
  const model = await AutoModelForCausalLM.from_pretrained(modelName);
  const prompt = 'You are interviewing a security researcher about advanced steganography techniques.';
  const secret = 'Hello World';

  console.log(`Secret to hide: ${secret}\n`);
  const [cover, recovered] = await generateStegoText(model, tokenizer, prompt, secret);
  console.log('--- Generated Cover Text ---');
  console.log(cover);
  console.log('\n--- Recovered Secret ---');
  console.log(recovered);
}

main();
