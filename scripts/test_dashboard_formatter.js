#!/usr/bin/env node
const assert = require('node:assert/strict');
const {formatDifficulty} = require('../jjmining-ltc-doge-p2pool/dashboard/format.js');

const cases = [
  [null, '—'],
  [0, '0 diff'],
  [29.870202947391988, '29.87 diff'],
  [999, '999.0 diff'],
  [1000, '1.00 K diff'],
  [29870, '29.87 K diff'],
  [1e6, '1.00 M diff'],
  [127e6, '127.0 M diff'],
  [1e9, '1.00 G diff'],
  [1e12, '1.00 T diff'],
  [1e15, '1.00 P diff'],
  [1e18, '1.00 E diff'],
  [1e21, '1.00 Z diff'],
  [1e24, '1.00 Y diff'],
  [-1, '—'],
  [NaN, '—'],
  [Infinity, '—'],
  ['not-a-number', '—'],
];

for (const [input, expected] of cases) assert.equal(formatDifficulty(input), expected);
console.log('Dashboard difficulty formatter tests passed');
