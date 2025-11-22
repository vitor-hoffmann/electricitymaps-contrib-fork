import * as fs from 'node:fs';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';

import { afterAll,beforeAll, describe, expect, it } from 'vitest';

import { getConfig } from '../scripts/generateZonesConfig';
import { generateAggregates } from './generateAggregates';
import { generateTopojson } from './generateTopojson';
import { WorldFeatureCollection } from './types';
import { getJSON } from './utilities';

const TEMP_DIR =
  'C:/Users/Usuario/.gemini/tmp/5432eed93d9745baeee6d23d05e83e6c9f94d2fb78087daf29a1857f542dc56e';
const TEST_WORLD_OUT_PATH = path.resolve(TEMP_DIR, 'test-world.json');

describe('generateTopojson', () => {
  let originalWorldFc: WorldFeatureCollection;
  let config;

  const __filename = fileURLToPath(import.meta.url);
  const __dirname = path.dirname(__filename);

  beforeAll(() => {
    originalWorldFc = getJSON(path.resolve(__dirname, 'world.geojson'));
    config = getConfig();
  });

  afterAll(() => {
    // Clean up the temporary file
    if (fs.existsSync(TEST_WORLD_OUT_PATH)) {
      fs.unlinkSync(TEST_WORLD_OUT_PATH);
    }
  });

  it('should calculate the correct center for the aggregated US zone', () => {
    // Step 1: Create the aggregated features, similar to generateWorld.ts
    const aggregatedFeatures = generateAggregates(originalWorldFc, config.zones);
    const worldFC: WorldFeatureCollection = {
      type: 'FeatureCollection',
      features: aggregatedFeatures,
    };

    // Step 2: Run generateTopojson to create the output file
    generateTopojson(worldFC, {
      OUT_PATH: TEST_WORLD_OUT_PATH,
      verifyNoUpdates: false,
    });

    // Step 3: Read the generated file and run assertions
    const resultTopo = getJSON(TEST_WORLD_OUT_PATH);

    const usCenter = resultTopo.objects.US?.properties?.center;
    expect(usCenter).toBeDefined();
    // This is the core of the test. With the buggy code, the center will be somewhere in Europe.
    // The expected value is the correct center of the contiguous US.
    expect(usCenter[0]).to.be.closeTo(-98.6, 1);
    expect(usCenter[1]).to.be.closeTo(39.8, 1);
  });
});
