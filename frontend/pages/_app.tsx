/**
 * Copyright (c) 2024 FootprintScan. All Rights Reserved.
 * 
 * This software and associated documentation files (the "Software") are proprietary
 * and confidential. Unauthorized copying, modification, distribution, or use of
 * this Software, via any medium, is strictly prohibited without express written
 * permission from the copyright holder.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
 */

import type { AppProps } from 'next/app';
import '../styles/globals.css';

export default function App({ Component, pageProps }: AppProps) {
  return <Component {...pageProps} />;
}

