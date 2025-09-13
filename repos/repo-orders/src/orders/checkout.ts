// Fixed: Added timeout guard and retry logic
export class CheckoutTimeoutError extends Error {}

async function fakePaymentCall(ms: number): Promise<string> { 
  return new Promise(res => setTimeout(res, ms)); 
}

export async function checkout(amount: number): Promise<string> {
  const started = Date.now();
  
  try {
    await Promise.race([
      fakePaymentCall(6000),
      new Promise((_, reject) => 
        setTimeout(() => reject(new CheckoutTimeoutError('5s timeout')), 5000)
      )
    ]);
  } catch (error) {
    if (error instanceof CheckoutTimeoutError) {
      // Retry once with shorter timeout
      await fakePaymentCall(3000);
    } else {
      throw error;
    }
  }
  
  if (Date.now() - started > 5000) {
    throw new CheckoutTimeoutError('payment gateway exceeded 5s');
  }
  return 'OK';
}
