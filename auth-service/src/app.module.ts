import { Module } from '@nestjs/common';
import { AuthController } from './auth.controller';
import { HealthController } from './health.controller';

@Module({
  controllers: [HealthController, AuthController]
})
export class AppModule {}

