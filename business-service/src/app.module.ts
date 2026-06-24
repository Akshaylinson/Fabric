import { Module } from '@nestjs/common';
import { BusinessController } from './business.controller';
import { HealthController } from './health.controller';

@Module({
  controllers: [HealthController, BusinessController]
})
export class AppModule {}

